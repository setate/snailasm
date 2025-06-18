const vscode = require('vscode');
const path = require('path');

console.log("🟢 SnailASM 확장 활성화됨");

function activate(context) {
  // 🧱 컴파일 명령 등록
  let disposable = vscode.commands.registerCommand('snailasm.compile', function () {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage("열린 파일이 없습니다.");
      return;
    }

    const compilerPath = path.join(__dirname, 'snailasm.py');
    const filePath = editor.document.fileName;

    const terminal = vscode.window.createTerminal("SnailASM Compile");
    terminal.show();
    terminal.sendText(`py "${compilerPath}" "${filePath}"`);
  });

  context.subscriptions.push(disposable);

  const instructions = [
  // R-type
  "add", "sub", "inc", "dec", "neg", "mul", "mulh", "div", "mod",
  "shl", "shr", "shl8", "shr8", "and", "or", "xor", "nor", "nand", "xnor", "not",
  "mov", "swap", "clr", "pcl", "stor", "load", "stors", "loads", "vga", "psl",
  "cmp", "ret", "push", "pop", "pushlr", "poplr",

  // I-type
  "jz", "jnz", "jmpr", "beq", "bne", "blt", "bgt", "ble", "bge",
  "addi", "subi", "li", "call", "callr",

  //pseudo_instruction
  "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "define", "macro", "endmacro"
];
  const completionProvider = vscode.languages.registerCompletionItemProvider(
    'snailASM',
    {
      provideCompletionItems(document, position) {
        return instructions.map(instr => {
          const item = new vscode.CompletionItem(instr, vscode.CompletionItemKind.Keyword);
          item.detail = "SnailASM instruction";
          return item;
        });
      }
    },
    ''
  );

  context.subscriptions.push(completionProvider);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
