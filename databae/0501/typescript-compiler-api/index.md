# TypeScript Compiler API 完全指南：从 AST 到代码生成

## 一、Compiler API 概述

### 1.1 什么是 Compiler API

TypeScript Compiler API 允许你程序式地操作 TypeScript 代码。

### 1.2 主要功能

- 解析代码为 AST
- 分析类型
- 代码转换
- 代码生成

---

## 二、创建项目

### 2.1 安装依赖

```bash
npm install typescript @types/node ts-node
```

### 2.2 基本结构

```typescript
import * as ts from 'typescript';

// 使用 ts 命名空间访问 API
```

---

## 三、解析代码

### 3.1 解析为 AST

```typescript
const code = `
  function greet(name: string) {
    return \`Hello, \${name}!\`;
  }
`;

const sourceFile = ts.createSourceFile(
  'test.ts',
  code,
  ts.ScriptTarget.ESNext,
  true
);

console.dir(sourceFile, { depth: null });
```

### 3.2 遍历 AST

```typescript
function traverse(node: ts.Node) {
  console.log(ts.SyntaxKind[node.kind], node.getText());
  
  ts.forEachChild(node, traverse);
}

traverse(sourceFile);
```

### 3.3 使用 ts-morph

```typescript
import { Project } from 'ts-morph';

const project = new Project();
const sourceFile = project.createSourceFile('test.ts', code);

console.log(sourceFile.getClasses());
console.log(sourceFile.getFunctions());
```

---

## 四、创建 AST 节点

### 4.1 创建函数

```typescript
const factory = ts.factory;

const functionDeclaration = factory.createFunctionDeclaration(
  undefined,
  undefined,
  factory.createIdentifier('greet'),
  undefined,
  [
    factory.createParameterDeclaration(
      undefined,
      undefined,
      factory.createIdentifier('name'),
      undefined,
      factory.createTypeReferenceNode('string'),
      undefined
    )
  ],
  factory.createTypeReferenceNode('string'),
  factory.createBlock([
    factory.createReturnStatement(
      factory.createNoSubstitutionTemplateLiteral('Hello, World!')
    )
  ])
);
```

### 4.2 创建类

```typescript
const classDeclaration = factory.createClassDeclaration(
  undefined,
  [factory.createModifier(ts.SyntaxKind.ExportKeyword)],
  factory.createIdentifier('User'),
  undefined,
  undefined,
  [
    factory.createPropertyDeclaration(
      undefined,
      [factory.createModifier(ts.SyntaxKind.PrivateKeyword)],
      factory.createIdentifier('name'),
      undefined,
      factory.createTypeReferenceNode('string'),
      undefined
    ),
    factory.createConstructorDeclaration(
      undefined,
      undefined,
      [
        factory.createParameterDeclaration(
          undefined,
          [factory.createModifier(ts.SyntaxKind.PrivateKeyword)],
          factory.createIdentifier('name'),
          undefined,
          factory.createTypeReferenceNode('string'),
          undefined
        )
      ],
      factory.createBlock([])
    )
  ]
);
```

---

## 五、代码转换

### 5.1 使用 Transformer

```typescript
const transformer: ts.TransformerFactory<ts.SourceFile> = (context) => {
  return (sourceFile) => {
    function visit(node: ts.Node): ts.Node {
      if (ts.isStringLiteral(node) && node.text === 'old') {
        return factory.createStringLiteral('new');
      }
      return ts.visitEachChild(node, visit, context);
    }
    
    return ts.visitNode(sourceFile, visit);
  };
};

const result = ts.transform(sourceFile, [transformer]);
```

### 5.2 代码生成

```typescript
const printer = ts.createPrinter();
const output = printer.printFile(result.transformed[0]);
console.log(output);
```

---

## 六、类型检查

### 6.1 创建 Program

```typescript
const program = ts.createProgram(['test.ts'], {
  target: ts.ScriptTarget.ESNext
});

const typeChecker = program.getTypeChecker();
```

### 6.2 获取类型

```typescript
const functionDecl = sourceFile.statements.find(
  (s): s is ts.FunctionDeclaration => ts.isFunctionDeclaration(s)
);

if (functionDecl) {
  const signature = typeChecker.getSignatureFromDeclaration(functionDecl)!;
  const returnType = typeChecker.getReturnTypeOfSignature(signature);
  console.log(typeChecker.typeToString(returnType));
}
```

---

## 七、实战项目：代码生成器

### 7.1 API 客户端生成

```typescript
import { Project, TypeGuards } from 'ts-morph';

function generateAPIClient(spec: APISpec) {
  const project = new Project();
  const file = project.createSourceFile('api.ts');
  
  spec.endpoints.forEach(endpoint => {
    const func = file.addFunction({
      name: endpoint.name,
      returnType: `Promise<${endpoint.responseType}>`,
      parameters: [
        { name: 'params', type: endpoint.paramsType }
      ]
    });
    
    func.addStatements([
      `return fetch('${endpoint.url}').then(r => r.json());`
    ]);
  });
  
  return file.getText();
}
```

### 7.2 装饰器处理器

```typescript
function processDecorators(sourceFile: ts.SourceFile) {
  const transformer: ts.TransformerFactory<ts.SourceFile> = (context) => {
    return (sourceFile) => {
      function visit(node: ts.Node): ts.Node {
        if (ts.isClassDeclaration(node)) {
          const members = node.members.map(member => {
            if (ts.isMethodDeclaration(member)) {
              const decorators = member.decorators;
              if (decorators) {
                // 处理装饰器逻辑
              }
            }
            return member;
          });
          
          return factory.updateClassDeclaration(
            node,
            node.decorators,
            node.modifiers,
            node.name,
            node.typeParameters,
            node.heritageClauses,
            members
          );
        }
        return ts.visitEachChild(node, visit, context);
      }
      
      return ts.visitNode(sourceFile, visit);
    };
  };
  
  return ts.transform(sourceFile, [transformer]);
}
```

---

## 八、高级技巧

### 8.1 诊断信息

```typescript
const diagnostics = ts.getPreEmitDiagnostics(program);

diagnostics.forEach(diagnostic => {
  const message = ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n');
  if (diagnostic.file) {
    const { line, character } = ts.getLineAndCharacterOfPosition(
      diagnostic.file,
      diagnostic.start!
    );
    console.log(`${diagnostic.file.fileName} (${line + 1}, ${character + 1}): ${message}`);
  } else {
    console.log(message);
  }
});
```

### 8.2 自定义编译器

```typescript
function compile(fileNames: string[], options: ts.CompilerOptions) {
  const program = ts.createProgram(fileNames, options);
  const emitResult = program.emit();
  
  const allDiagnostics = ts
    .getPreEmitDiagnostics(program)
    .concat(emitResult.diagnostics);
  
  return allDiagnostics;
}
```

---

## 总结

TypeScript Compiler API 提供了强大的代码操作能力，从简单的 AST 遍历到复杂的代码转换，都可以通过 API 实现。掌握这些技术可以帮助你构建强大的代码工具。
