import * as vscode from 'vscode';
import { BhashyaHoverProvider } from './hoverProvider';

export function activate(context: vscode.ExtensionContext): void {
    const pythonSelector: vscode.DocumentSelector = { language: 'python', scheme: 'file' };
    const teluguSelector: vscode.DocumentSelector = { language: 'telugu-python', scheme: 'file' };
    const sanskritSelector: vscode.DocumentSelector = { language: 'sanskrit-python', scheme: 'file' };

    const reverseHover = new BhashyaHoverProvider('reverse');
    const forwardHover = new BhashyaHoverProvider('forward');

    context.subscriptions.push(
        vscode.languages.registerHoverProvider(pythonSelector, reverseHover),
        vscode.languages.registerHoverProvider(teluguSelector, forwardHover),
        vscode.languages.registerHoverProvider(sanskritSelector, forwardHover),
    );
}

export function deactivate(): void {
    // nothing to clean up
}
