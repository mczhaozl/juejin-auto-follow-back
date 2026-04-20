# TypeScript Compiler API 完全指南

## 一、解析 TS 文件

```typescript
import * as ts from 'typescript';
import * as fs from 'fs';

const code = fs.readFileSync('input.ts', 'utf8');
const sourceFile = ts.createSourceFile(
  'input.ts',
  code,
  ts.ScriptTarget.ESNext,
  true
);
```

## 二、遍历 AST

```typescript
function traverse(node: ts.Node) {
  if (ts.isInterfaceDeclaration(node)) {
    console.log('Found interface:', node.name.getText());
  }
  
  node.forEachChild(traverse);
}

traverse(sourceFile);
```

## 三、创建节点

```typescript
const factory = ts.factory;

const interfaceNode = factory.createInterfaceDeclaration(
  undefined,
  [factory.createModifier(ts.SyntaxKind.ExportKeyword)],
  factory.createIdentifier('User'),
  undefined,
  undefined,
  [
    factory.createPropertySignature(
      undefined,
      factory.createIdentifier('name'),
      undefined,
      factory.createKeywordTypeNode(ts.SyntaxKind.StringKeyword)
    )
  ]
);
```

## 四、代码转换

```typescript
function transform(context: ts.TransformationContext) {
  return (rootNode: ts.SourceFile) => {
    function visit(node: ts.Node): ts.Node {
      if (ts.isClassDeclaration(node)) {
        // 修改类
      }
      return ts.visitEachChild(node, visit, context);
    }
    return ts.visitNode(rootNode, visit);
  };
}

const result = ts.transform(sourceFile, [transform]);
```

## 五、类型检查

```typescript
const program = ts.createProgram(['input.ts'], {});
const typeChecker = program.getTypeChecker();

const symbol = typeChecker.getSymbolAtLocation(sourceFile);
```

## 六、最佳实践

- 了解 TypeScript 的内部机制
- 使用工厂函数创建节点
- 处理各种节点类型
- 调试使用 ts-node 或 ts-ast-viewer
- 考虑性能：避免大型转换
- 版本兼容性
