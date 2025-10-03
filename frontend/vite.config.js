import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import EnvironmentPlugin from 'vite-plugin-environment';
import path from 'path';

export default defineConfig({
	plugins: [
		sveltekit(),
		EnvironmentPlugin('all', { prefix: 'CANISTER_' }),
		EnvironmentPlugin('all', { prefix: 'DFX_' }),
	],
	resolve: {
		alias: {
			'declarations': path.resolve(__dirname, '../src/declarations'),
		},
	},
	optimizeDeps: {
		esbuildOptions: {
			define: {
				global: 'globalThis',
			},
		},
	},
	server: {
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:4943',
				changeOrigin: true,
			},
		},
	},
});
