// adb-shell.js - Interactive ADB shell in browser
const exec = require('child_process').exec;
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function adb(cmd, cb) {
  exec(`adb shell ${cmd}`, (err, stdout, stderr) => {
    cb(stdout + stderr);
  });
}

console.log("ADB Interactive Shell (type 'quit' to exit)");
function prompt() {
  rl.question('$ ', (input) => {
    if (input === 'quit') { rl.close(); return; }
    adb(input, (out) => {
      console.log(out);
      prompt();
    });
  });
}
prompt();
