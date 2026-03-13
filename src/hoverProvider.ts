import * as vscode from 'vscode';
import { Translator } from './translator';

/**
 * Provides hover tooltips that show the translated version of the hovered line.
 *
 * direction = 'forward'  → Indian-language file hovered → show Python translation
 * direction = 'reverse'  → Python file hovered          → show Indian-language translation
 */
export class BhashyaHoverProvider implements vscode.HoverProvider {
    private translator = new Translator();

    constructor(private direction: 'forward' | 'reverse') {}

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken,
    ): Promise<vscode.Hover | null> {
        const source = document.getText();
        if (!source.trim()) {
            return null;
        }

        const lang = this.resolveLanguage(document);
        const cacheKey = `${document.uri.toString()}@${document.version}`;

        const result = await this.translator.translate(this.direction, source, lang, cacheKey);
        if (!result) {
            return null;
        }

        const hoveredLine = position.line;

        // Show a context window: the hovered line ±2 surrounding lines from
        // the translated output, so the popup is useful but not overwhelming.
        const contextRadius = 2;
        const startLine = Math.max(0, hoveredLine - contextRadius);
        const endLine = Math.min(result.lines.length - 1, hoveredLine + contextRadius);

        if (hoveredLine >= result.lines.length) {
            return null;
        }

        const snippetLines: string[] = [];
        for (let i = startLine; i <= endLine; i++) {
            const prefix = i === hoveredLine ? '▶ ' : '  ';
            snippetLines.push(`${prefix}${result.lines[i]}`);
        }

        const langId = this.direction === 'forward' ? 'python' : 'plaintext';
        const header = this.direction === 'forward'
            ? '**Bhashyapyc: Python Translation**'
            : `**Bhashyapyc: ${lang === 'sa' ? 'Sanskrit' : 'Telugu'} Translation**`;

        const markdown = new vscode.MarkdownString();
        markdown.appendMarkdown(`${header}\n\n`);
        markdown.appendCodeblock(snippetLines.join('\n'), langId);
        markdown.isTrusted = true;

        const lineRange = document.lineAt(hoveredLine).range;
        return new vscode.Hover(markdown, lineRange);
    }

    /**
     * Determine the translation language code.
     *
     * For forward translation, detect from file extension or document language ID.
     * For reverse translation, use the user's configured target language.
     */
    private resolveLanguage(document: vscode.TextDocument): string {
        if (this.direction === 'forward') {
            const langId = document.languageId;
            if (langId === 'sanskrit-python' || document.fileName.endsWith('.sapy')) {
                return 'sa';
            }
            // Default to auto-detection for Telugu / unknown
            return 'auto';
        }

        // Reverse: use configured target language
        return vscode.workspace
            .getConfiguration('bhashyapyc')
            .get<string>('targetLanguage', 'te');
    }
}
