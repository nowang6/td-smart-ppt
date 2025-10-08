// demo.ts
var UserManager = class {
  users = [];
  addUser(user) {
    this.users.push(user);
    console.log(`\u7528\u6237 ${user.name} \u5DF2\u6DFB\u52A0`);
  }
  getAllUsers() {
    return this.users;
  }
  findUserByName(name) {
    return this.users.find((user) => user.name === name);
  }
};
var userManager = new UserManager();
userManager.addUser({
  name: "\u5F20\u4E09",
  age: 25,
  email: "zhangsan@example.com"
});
userManager.addUser({
  name: "\u674E\u56DB",
  age: 30,
  email: "lisi@example.com"
});
console.log("\u6240\u6709\u7528\u6237:", userManager.getAllUsers());
console.log("\u67E5\u627E\u7528\u6237:", userManager.findUserByName("\u5F20\u4E09"));
export {
  UserManager
};
