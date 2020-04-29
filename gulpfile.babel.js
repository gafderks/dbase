import gulp from 'gulp';
// js
import rollupStream from '@rollup/stream';
import babel from 'rollup-plugin-babel';
import uglify from 'gulp-uglify';
import rename from 'gulp-rename';
import sourcemaps from 'gulp-sourcemaps';
import source from 'vinyl-source-stream';
import buffer from 'vinyl-buffer';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import inject from '@rollup/plugin-inject';
import alias from '@rollup/plugin-alias';
import merge from 'merge-stream';
// sass
import postcss from 'gulp-postcss';
import sass from 'gulp-sass';
import cssnano from 'cssnano';
import autoprefixer from 'autoprefixer';
import atImport from 'postcss-import';
import tildeImporter from 'node-sass-tilde-importer';
import pixrem from 'pixrem';
// other
import imagemin from 'gulp-imagemin';
import del from 'del';
import browserSync from 'browser-sync';

import booking from './booking/static/booking/config.gulp';
import dbase from './dbase/static/dbase/config.gulp';
import camera from './camera/static/camera/config.gulp';

const configs = [booking, dbase, camera];

const aliases = configs.filter(config => config.alias).map(config => config.alias);

const server = browserSync.create();

function serve(done) {
  server.init({
    notify: false,
    proxy: '127.0.0.1:8000',
    reloadDelay: 300,
    reloadDebounce: 500,
  });
  done();
}

function reload(done) {
  server.reload();
  done();
}

function scripts() {
  const tasks = configs.filter(config => config.scripts).map(config => config.scripts).map(config => {
    return rollupStream({
      input: config.srcDir + '/' + config.entry,
      output: {
        sourcemap: true,
        format: 'umd',
      },
      context: 'window',
      plugins: [
        inject(
          {
            $: 'jquery',
            jQuery: 'jquery'
          }
        ),
        alias({
          entries: aliases
        }),
        babel({
          exclude: 'node_modules/**'
        }),
        resolve(), commonjs()
      ],
    }).pipe(source(config.entry, config.srcDir))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
      .pipe(gulp.dest(config.dest)) // save .js
      .pipe(uglify({ output: {comments: 'some'} }))
      .pipe(rename({suffix: '.min'}))
      .pipe(sourcemaps.write('.'))
      .pipe(gulp.dest(config.dest)); // save .min.js
  });

  return merge(tasks);

}

function styles() {
  const processors = [
    atImport,
    pixrem,
    autoprefixer,
    cssnano
  ];

  const tasks = configs.filter(config => config.styles).map(config => config.styles).map(config => {
    return gulp.src(config.src)
      .pipe(sourcemaps.init())
      .pipe(sass({
        includePaths: ['node_modules'], importer: tildeImporter
      }).on('error', sass.logError))
      .pipe(postcss(processors))
      .pipe(rename({suffix: '.min'}))
      .pipe(sourcemaps.write('.'))
      .pipe(gulp.dest(config.dest))
      .pipe(server.stream());
  });

  return merge(tasks);
}

function images() {
  const tasks = configs.filter(config => config.images).map(config => config.images).map(config => {
    return gulp.src(config.src)
      .pipe(imagemin())
      .pipe(gulp.dest(config.dest));
  });

  return merge(tasks);
}

function watch() {
  // Scripts
  gulp.watch(
    ['**/static/**/*.js'],
    gulp.series(scripts, reload)
  );
  // Styles
  gulp.watch(
    ['**/static/**/*.css', '**/static/**/*.scss'],
    styles
  );
  // Pages
  gulp.watch(
    ['**/*.html'],
    reload
  );
}

const clean = () => del(['build']);
const build = gulp.parallel(scripts, styles, images);

const dev = gulp.series(serve, watch);

export {scripts, styles, images, clean, build, dev};
export default build;
