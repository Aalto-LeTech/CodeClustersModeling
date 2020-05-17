# -*- coding: utf-8 -*-

from server.services.antlr_local.generated.JavaParserListener import JavaParserListener
from server.services.antlr_local.generated.JavaParser import JavaParser

class Node(object):
    def __init__(self, parent, label, depth=0):
        self.label = label
        self.children = []
        self.parent = parent
        self.depth = depth

    def addChild(self, node):
        self.children.append(node)
        return self
    
    def getParent(self):
        return self.parent
    
    def __str__(self):
        n = f'{self.depth}:{self.label}'
        s = '\n'.join([n]+[str(c) for c in self.children])
        padding = ' ' * self.depth
        return f'{padding} {s}'
    
    def __len__(self):
        return 1 + sum([len(c) for c in self.children])

class TreeListener(JavaParserListener):    
    
    def __init__(self):
        self.tree = Node(None, 'root', 0)
        self.currentNode = self.tree
        self.currentDepth = 1

    def reset(self):
        self.tree = Node(None, 'root', 0)
        self.currentNode = self.tree
        self.currentDepth = 1

    def _addNode(self, name):
        n = Node(self.currentNode, name, self.currentDepth)
        self.currentNode.addChild(n)

    def _enterNode(self, name):
        n = Node(self.currentNode, name, self.currentDepth)
        self.currentNode.addChild(n)
        self.currentNode = n
        self.currentDepth += 1

    def _exitNode(self, name):
        prev = self.currentNode.getParent()
        n = Node(prev, name, self.currentDepth - 1)
        prev.addChild(n)
        self.currentNode = n
        self.currentDepth -= 1

    def enterVariableDeclarators(self, ctx):
        self.res = self._addNode("VARDEF ")
        
    def enterAnnotation(self, ctx):
        self.res = self._addNode("ANNO    ")
        
    def enterClassDeclaration(self, ctx):
        self.res = self._enterNode("CLASS{  ")
        
    def exitClassDeclaration(self, ctx):
        self.res = self._exitNode("}CLASS  ")
            
    def enterImportDeclaration(self, ctx):
        self.res = self._addNode("IMPORT  ")
        
    def enterPackageDeclaration(self, ctx):
        self.res = self._addNode("PACKAGE ")
        
    def enterConstantDeclarator(self, ctx):
        self.res = self._addNode("VARDEF ")
        
    def enterClassCreatorRest(self, ctx):
        if ctx.classBody():
            self.res = self._enterNode("INCLASS{")
            
    def exitClassCreatorRest(self, ctx):
        if ctx.classBody():
            self.res = self._exitNode("}INCLASS")
                
    def enterCatchClause(self, ctx):
        self.res = self._enterNode("CATCH{  ")
        
    def exitCatchClause(self, ctx):
        self.res = self._exitNode("}CATCH  ")
            
    def enterEnumConstants(self, ctx):
        self.res = self._addNode("ENUM_CLA")
        
    def enterEnumDeclaration(self, ctx):
        self.res = self._enterNode("ENUM{   ")
        
    def exitEnumDeclaration(self, ctx):
        self.res = self._exitNode("}ENUM   ")
            
    def enterExplicitConstructorInvocation(self, ctx):
        self.res = self._addNode("APPLY   ")
        
    def enterVariableInitializer(self, ctx):
        if not isinstance(ctx.parentCtx, JavaParser.ArrayInitializerContext):
            self.res = self._addNode("ASSIGN  ")
            
    def enterCreator(self, ctx):
        if ctx.classCreatorRest():
            self.res = self._addNode("NEWCLASS")
        elif ctx.arrayCreatorRest():
            self.res = self._addNode("NEWARRAY")
    
    def enterTryStatement(self, ctx):
        self.res = self._enterNode("TRY{    ")        
            
    def exitTryStatement(self, ctx):
        self.res = self._exitNode("FINALLY ")   
        
    def enterNormalInterfaceDeclaration(self, ctx):
        self.res = self._enterNode("INTERF{ ")        
            
    def exitNormalInterfaceDeclaration(self, ctx):
        self.res = self._exitNode("}INTERF ") 
            
    def enterExplicitGenericInvocation(self, ctx):
        self.res = self._addNode("APPLY   ") 
                    
    def enterMethodDeclaration(self, ctx):
        if ctx.start.text == "void":
            self.res = self._addNode("VOID    ")
        self.res = self._enterNode("METHOD{ ")
    
    def exitMethodDeclaration(self, ctx):
        self.res = self._exitNode("}METHOD ")
            
    def exitSwitchLabel(self, ctx):
        self.res = self._addNode("CASE    ")

    def enterConstructorDeclaration(self, ctx):
        self.res = self._enterNode("CONSTR{ ")
         
    def exitConstructorDeclaration(self, ctx):
        self.res = self._exitNode("}CONSTR ")
            
    def enterResource(self, ctx):
        self.res = self._addNode("TRY_RES ")
            
    def enterArrayInitializer(self, ctx):
        self.res = self._enterNode("ARRINIT{")
    
    def exitArrayInitializer(self, ctx):
        self.res = self._exitNode("ARRINIT}")
            
    def enterTypeArgument(self, ctx):
        if isinstance(ctx.parentCtx.parentCtx, JavaParser.CreatedNameContext):
            pass
        else:
            self.res = self._addNode("GENERIC ")
    
    def enterStatement(self, ctx):
        if ctx.FOR():
            self.res = self._enterNode("LOOP{ ")
        elif ctx.IF():
            self.res = self._enterNode("IF{     ")
        elif ctx.THROW():
            self.res = self._addNode("THROW   ")
        elif ctx.BREAK():
            self.res = self._addNode("BREAK   ")
        elif ctx.RETURN():
            self.res = self._addNode("RETURN  ")
        elif ctx.CONTINUE():
            self.res = self._addNode("CONTINUE")
        elif ctx.DO():
            self.res = self._enterNode("LOOP{ ")
        elif ctx.SWITCH():
            self.res = self._enterNode("SWITCH{ ")
        elif ctx.WHILE():
            self.res = self._enterNode("LOOP{ ")
        
    def exitStatement(self, ctx):
        if ctx.FOR():
            self.res = self._exitNode("}LOOP ")
        elif ctx.IF():
            self.res = self._exitNode("}IF     ")
        elif ctx.DO():
            self.res = self._exitNode("}LOOP ")
        elif ctx.SWITCH():
            self.res = self._exitNode("}SWITCH ")
        elif ctx.WHILE():
            self.res = self._exitNode("}LOOP ")
    
    def enterExpression(self, ctx):
        if ctx.bop: # has operator
            exprs = ctx.bop.text
            if "=" in exprs:
                self.res = self._addNode("ASSIGN  ")
            elif "?" in exprs or ":" in exprs:
                self.res = self._addNode("COND    ")
    
    def enterMethodCall(self, ctx):
        self.res = self._addNode("APPLY   ")
        
    def enterClassBodyDeclaration(self, ctx):
        if ctx.STATIC():
            self.res = self._enterNode("INIT{   ")
            
    def exitClassBodyDeclaration(self, ctx):
        if ctx.STATIC():
            self.res = self._exitNode("}INIT   ")
                
    def get_tree(self):
        return self.tree