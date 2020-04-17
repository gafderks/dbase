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
// sass
import postcss from 'gulp-postcss';
import sass from 'gulp-sass';
import cssnano from 'cssnano';
import autoprefixer from 'autoprefixer';
import atImport from 'postcss-import';
import tildeImporter from 'node-sass-tilde-importer';

import booking from './booking/static/booking/config.gulp';
import dbase from './dbase/static/dbase/config.gulp';
import camera from './camera/static/camera/config.gulp';

const configs = [booking, dbase, camera];

const aliases = configs.map(config => config.alias);

function scripts(done) {
  const tasks = configs.map(config => {
    function bundleApp(taskDone) {
      rollupStream({
        input: config.scripts.srcDir + '/' + config.scripts.entry,
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
      }).pipe(source(config.scripts.entry, config.scripts.srcDir))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(gulp.dest(config.scripts.dest)) // save .js
        .pipe(uglify({ output: {comments: 'some'} }))
        .pipe(rename({suffix: '.min'}))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.scripts.dest)); // save .min.js
      taskDone();
    }
    // Use function.displayName to customize the task name
    bundleApp.displayName = `scripts > ${config.app_name}`;
    return bundleApp;
  });

  return gulp.series(...tasks, (seriesDone) => {
    seriesDone();
    done();
  })();

}

function styles(done) {
  const processors = [
    atImport,
    autoprefixer,
    cssnano
  ];

  const tasks = configs.map(config => {
    function bundleCSS(taskDone) {
      gulp.src(config.styles.src)
        .pipe(sourcemaps.init())
        .pipe(sass({
          includePaths: ['node_modules'], importer: tildeImporter
        }).on('error', sass.logError))
        .pipe(postcss(processors))
        .pipe(rename({suffix: '.min'}))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.styles.dest));
      taskDone();
    }
    // Use function.displayName to customize the task name
    bundleCSS.displayName = `styles > ${config.app_name}`;
    return bundleCSS;
  });

  return gulp.series(...tasks, (seriesDone) => {
    seriesDone();
    done();
  })();

}

const build = gulp.parallel(scripts, styles);

export {scripts, styles, build};
export default build;
