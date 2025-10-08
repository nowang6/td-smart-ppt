import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";
import { setOutlines } from "@/store/slices/presentationGeneration";
import { jsonrepair } from "jsonrepair";
import { RootState } from "@/store/store";

export const useOutlineStreaming = (presentationId: string | null) => {
  const dispatch = useDispatch();
  const { outlines } = useSelector((state: RootState) => state.presentationGeneration);
  const [isStreaming, setIsStreaming] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [activeSlideIndex, setActiveSlideIndex] = useState<number | null>(null);
  const [highestActiveIndex, setHighestActiveIndex] = useState<number>(-1);
  const prevSlidesRef = useRef<{ content: string }[]>([]);
  const activeIndexRef = useRef<number>(-1);
  const highestIndexRef = useRef<number>(-1);

  useEffect(() => {
    if (!presentationId || outlines.length > 0) return;

    let abortController: AbortController;
    let accumulatedArgs = "";

    const initializeStream = async () => {
      setIsStreaming(true)
      setIsLoading(true)
      try {
        abortController = new AbortController();
        
        const response = await fetch(`/api/v1/outlines/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            "threadId": "thread-12345",
            "runId": "run-67890",
            "state": {},
            "messages": [
              {
                "id": presentationId,
                "role": "user",
                "content": ""
              }
            ],
            "tools": [],
            "context": [],
            "forwardedProps": {}
          }),
          signal: abortController.signal
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body reader available');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim() === '') continue;
            
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6);
              if (dataStr === '[DONE]') {
                setIsStreaming(false);
                setIsLoading(false);
                setActiveSlideIndex(null);
                setHighestActiveIndex(-1);
                activeIndexRef.current = -1;
                highestIndexRef.current = -1;
                return;
              }

              try {
                const data = JSON.parse(dataStr);
                switch (data.type) {
                  case "RUN_STARTED":
                    // Run has started, continue processing
                    break;

                  case "TEXT_MESSAGE_START":
                    // Text message started, continue processing
                    break;

                  case "TEXT_MESSAGE_END":
                    // Text message ended, continue processing
                    break;

                  case "TOOL_CALL_START":
                    // Tool call started, reset accumulated args
                    accumulatedArgs = "";
                    break;

                  case "TOOL_CALL_ARGS":
                    // Accumulate delta chunks
                    if (data.delta) {
                      accumulatedArgs += data.delta;
                      
                      // Try to parse the accumulated JSON
                      try {
                        const repairedJson = jsonrepair(accumulatedArgs);
                        const partialData = JSON.parse(repairedJson);

                        if (partialData.slides) {
                          const nextSlides: { content: string }[] = partialData.slides || [];
                          try {
                            const prev = prevSlidesRef.current || [];
                            let changedIndex: number | null = null;
                            const maxLen = Math.max(prev.length, nextSlides.length);
                            for (let i = 0; i < maxLen; i++) {
                              const prevContent = prev[i]?.content;
                              const nextContent = nextSlides[i]?.content;
                              if (nextContent !== prevContent) {
                                changedIndex = i;
                              }
                            }
                            const prevActive = activeIndexRef.current;
                            let nextActive = changedIndex ?? prevActive;
                            if (nextActive < prevActive) {
                              nextActive = prevActive;
                            }
                            activeIndexRef.current = nextActive;
                            setActiveSlideIndex(nextActive);

                            if (nextActive > highestIndexRef.current) {
                              highestIndexRef.current = nextActive;
                              setHighestActiveIndex(nextActive);
                            }
                          } catch { }

                          prevSlidesRef.current = nextSlides;
                          dispatch(setOutlines(nextSlides));
                          setIsLoading(false);
                        }
                      } catch (error) {
                        // JSON isn't complete yet, continue accumulating
                      }
                    }
                    break;

                  case "TOOL_CALL_END":
                    // Tool call completed, process final accumulated args
                    try {
                      const repairedJson = jsonrepair(accumulatedArgs);
                      const finalData = JSON.parse(repairedJson);
                      
                      if (finalData.slides) {
                        const outlinesData: { content: string }[] = finalData.slides;
                        dispatch(setOutlines(outlinesData));
                        setIsStreaming(false);
                        setIsLoading(false);
                        setActiveSlideIndex(null);
                        setHighestActiveIndex(-1);
                        prevSlidesRef.current = outlinesData;
                        activeIndexRef.current = -1;
                        highestIndexRef.current = -1;
                        return;
                      }
                    } catch (error) {
                      console.error("Error parsing final tool call args:", error);
                      toast.error("Failed to parse presentation data");
                      return;
                    }
                    break;

                  case "error":
                    setIsStreaming(false);
                    setIsLoading(false);
                    setActiveSlideIndex(null);
                    setHighestActiveIndex(-1);
                    activeIndexRef.current = -1;
                    highestIndexRef.current = -1;
                    toast.error('Error in outline streaming', {
                      description: data.detail || 'Failed to connect to the server. Please try again.',
                    });
                    return;
                }
              } catch (error) {
                console.error('Error parsing SSE data:', error);
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          // Request was aborted, this is expected
          return;
        }
        
        setIsStreaming(false);
        setIsLoading(false);
        setActiveSlideIndex(null);
        setHighestActiveIndex(-1);
        activeIndexRef.current = -1;
        highestIndexRef.current = -1;
        toast.error("Failed to initialize connection");
      }
    };

    initializeStream();
    
    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [presentationId, dispatch]);

  return { isStreaming, isLoading, activeSlideIndex, highestActiveIndex };
}; 