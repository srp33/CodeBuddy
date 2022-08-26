import type * as monaco from 'monaco-editor';

declare global {
    interface Window {
		templateData: any;
		monaco: typeof monaco;
	}
}

export {}
