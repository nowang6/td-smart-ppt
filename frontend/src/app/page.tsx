import Image from "next/image";

export default function Home() {
  return (
    <div className="container-fluid">
      {/* Bootstrap Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container">
          <a className="navbar-brand" href="#" title="Next.js Home">
            <Image
              className="dark:invert"
              src="/next.svg"
              alt="Next.js logo"
              width={120}
              height={25}
              priority
            />
          </a>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <a className="nav-link active" aria-current="page" href="#">
                  Home
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link" href="#">
                  Features
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link" href="#">
                  About
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Bootstrap Hero Section */}
      <div className="jumbotron bg-primary text-white text-center py-5">
        <div className="container">
          <h1 className="display-4">Welcome to Next.js with Bootstrap!</h1>
          <p className="lead">
            This is a Next.js project initialized with Yarn and configured with Bootstrap CSS framework.
          </p>
          <hr className="my-4" />
          <p>
            You can now use both Tailwind CSS and Bootstrap classes in your components.
          </p>
          <a className="btn btn-light btn-lg" href="#" role="button">
            Learn more
          </a>
        </div>
      </div>

      {/* Bootstrap Cards Section */}
      <div className="container my-5">
        <div className="row">
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Next.js</h5>
                <p className="card-text">
                  A React framework for production with hybrid static & server rendering.
                </p>
                <a href="https://nextjs.org" className="btn btn-primary">
                  Learn More
                </a>
              </div>
            </div>
          </div>
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Bootstrap</h5>
                <p className="card-text">
                  The world's most popular front-end component library.
                </p>
                <a href="https://getbootstrap.com" className="btn btn-primary">
                  Learn More
                </a>
              </div>
            </div>
          </div>
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">TypeScript</h5>
                <p className="card-text">
                  Typed JavaScript at any scale for better development experience.
                </p>
                <a href="https://www.typescriptlang.org" className="btn btn-primary">
                  Learn More
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bootstrap Alert */}
      <div className="container">
        <div className="alert alert-success" role="alert">
          <h4 className="alert-heading">Setup Complete!</h4>
          <p>
            Your Next.js project has been successfully initialized with Yarn and configured with Bootstrap CSS.
            You can now start building your application using Bootstrap components and utilities.
          </p>
          <hr />
          <p className="mb-0">
            Check the <code>src/app/page.tsx</code> file to see Bootstrap components in action.
          </p>
        </div>
      </div>
    </div>
  );
}
