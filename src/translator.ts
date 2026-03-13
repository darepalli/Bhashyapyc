import { execFile } from 'child_process';
import * as vscode from 'vscode';

/**
 * Result of a translation operation.
 */
export interface TranslationResult {
    /** The full translated source text. */
    translatedSource: string;
    /** Individual translated lines (split from translatedSource). */
    lines: string[];
}

/**
 * Translates source code between Python and Indian languages by invoking the
 * bhashyapyc Python package in a subprocess.
 *
 * Results are cached per (document URI + version) to avoid repeated subprocess calls.
 */
export class Translator {
    /**
     * Cache keyed by `${uri}@${version}@${direction}@${lang}`.
     */
    private cache = new Map<string, TranslationResult>();

    /**
     * Translate the full document text.
     *
     * @param direction - 'forward' (Indian→Python) or 'reverse' (Python→Indian)
     * @param source - source text to translate
     * @param lang - language code: 'te', 'sa', or 'auto'
     * @param cacheKey - optional cache key (uri@version) to enable caching
     * @returns The translation result or null on error.
     */
    async translate(
        direction: 'forward' | 'reverse',
        source: string,
        lang: string,
        cacheKey?: string,
    ): Promise<TranslationResult | null> {
        const fullKey = cacheKey ? `${cacheKey}@${direction}@${lang}` : undefined;

        if (fullKey && this.cache.has(fullKey)) {
            return this.cache.get(fullKey)!;
        }

        const pythonPath = vscode.workspace
            .getConfiguration('bhashyapyc')
            .get<string>('pythonPath', 'python3');

        const pyScript = direction === 'forward'
            ? `
import sys, json
from bhashyapyc.compiler import compile_to_python
src = sys.stdin.read()
print(compile_to_python(src, lang=${JSON.stringify(lang)}), end='')
`
            : `
import sys
from bhashyapyc.reverse import reverse_translate_python
src = sys.stdin.read()
print(reverse_translate_python(src, lang=${JSON.stringify(lang)}), end='')
`;

        try {
            const translated = await this.runPython(pythonPath, pyScript, source);
            const result: TranslationResult = {
                translatedSource: translated,
                lines: translated.split('\n'),
            };

            if (fullKey) {
                this.cache.set(fullKey, result);
            }
            return result;
        } catch {
            return null;
        }
    }

    /**
     * Invalidate cached translations for a document.
     */
    invalidate(uri: string): void {
        for (const key of this.cache.keys()) {
            if (key.startsWith(uri)) {
                this.cache.delete(key);
            }
        }
    }

    private runPython(pythonPath: string, script: string, stdin: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const proc = execFile(
                pythonPath,
                ['-c', script],
                { maxBuffer: 10 * 1024 * 1024 },
                (error, stdout, stderr) => {
                    if (error) {
                        reject(new Error(stderr || error.message));
                    } else {
                        resolve(stdout);
                    }
                },
            );
            if (proc.stdin) {
                proc.stdin.write(stdin);
                proc.stdin.end();
            }
        });
    }
}
