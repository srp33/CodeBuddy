const esbuild = require('esbuild');
const assetsManifest = require('esbuild-plugin-assets-manifest');
const { sassPlugin } = require('esbuild-sass-plugin');
const { copy } = require('esbuild-plugin-copy');



const isProdBuild = process.env.NODE_ENV === 'production';

esbuild.build({
	assetNames: '[dir]/[name]',
	entryNames: '[dir]/[name]',
	// assetNames: isProdBuild ? '[dir]/[name]-[hash]' : '[dir]/[name]',
	// entryNames: isProdBuild ? '[dir]/[name]-[hash]' : '[dir]/[name]',
    entryPoints: {
		shared: 'ui/shared/index.js',

		'css/mystyles': 'ui/css/mystyles.scss',
		'css/styles': 'ui/css/styles.css',
		'css/bulma-tooltip': 'ui/css/bulma-tooltip.scss',
		'css/profile-styles': 'ui/css/profile-styles.css',
		'css/modal': 'ui/css/modal.css',
		'css/timer': 'ui/css/timer.css',
	},
    bundle: true,
    outdir: 'static/',
	outbase: 'ui/',
	target: ['es2015'],
	minify: isProdBuild,
	sourcemap: isProdBuild ? false : 'inline',
	watch: isProdBuild ? false : {
		onRebuild(error, result) {
			if (error) {
				console.error('watch build error')
			} else {
				console.log(`rebuilt successfully`)
			}
		},
	},
    plugins: [
		assetsManifest({
			filename: 'manifest.json',
			path: './static',
			metadata: { timestamp: new Date() },
		}),
		sassPlugin(),
		copy({
			once: true,
			assets: [
				{
					from: ['./ui/images/*'],
					to: ['.'],
				},
				{
					from: ['./node_modules/ace-builds/src-noconflict/**/*.js'],
					to: './ace/',
					keepStructure: true,
				},
			],
		}),
	],
}).catch((e) => console.error(e.message));