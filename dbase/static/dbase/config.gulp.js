export default {
  app_name: 'dbase',
  alias: {
    find: 'dbase', replacement: '../../../../dbase/static/dbase/js'
  },
  scripts: {
    srcDir: './dbase/static/dbase/js',
    entry: 'app.js',
    dest: './build/dbase/js/'
  },
  styles: {
    src: './dbase/static/dbase/css/app.scss',
    dest: './build/dbase/css/'
  }
};
