import gulp from 'gulp';
// js
import rollupStream from '@rollup/stream';
import babel from 'rollup-plugin-babel';
import terser from 'gulp-terser';
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
import sass from 'gulp-dart-sass';
import cssnano from 'cssnano';
import autoprefixer from 'autoprefixer';
import atImport from 'postcss-import';
import pixrem from 'pixrem';
// other
import imagemin from 'gulp-imagemin';
import {deleteAsync as del} from 'del';
import browserSync from 'browser-sync';

import booking from './booking/static/booking/config.gulp.js';
import dbase from './dbase/static/dbase/config.gulp.js';
import camera from './camera/static/camera/config.gulp.js';
import catalog from './catalog/static/catalog/config.gulp.js';

const configs = [booking, dbase, camera, catalog];

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

// Flatten an array with potential subarrays
const flatten = (arr) =>  arr.reduce((flat, next) => flat.concat(next), []);

function extract_tasks_from_configs(task_type) {
  // Get the configs that have a task with the specified type and return the tasks therefore
  const tasks_per_config = configs.filter(config => config[task_type]).map(config => config[task_type]);
  // Flatten the tasks as some tasks may be arrays of tasks
  return flatten(tasks_per_config);
}

function scripts() {
  const tasks = extract_tasks_from_configs('scripts').map(config => {
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
      .pipe(terser())
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

  const tasks = extract_tasks_from_configs('styles').map(config => {
    return gulp.src(config.src)
      .pipe(sourcemaps.init())
      .pipe(sass({
        includePaths: ['node_modules']
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
  const tasks = extract_tasks_from_configs('images').map(config => {
    return gulp.src(config.src)
      .pipe(imagemin())
      .pipe(gulp.dest(config.dest));
  });

  return merge(tasks);
}

function staticFiles() {
  let tasks = [];
  configs.filter(config => config.staticFiles).map(config => config.staticFiles).map(config => {
    config.map(files => {
      tasks.push(gulp.src(files.src)
        .pipe(gulp.dest(files.dest)));
    });
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
const build = gulp.parallel(scripts, styles, images, staticFiles);

const dev = gulp.series(serve, watch);

export {scripts, styles, images, staticFiles, clean, build, dev};
export default build;
