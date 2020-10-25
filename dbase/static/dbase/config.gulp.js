export default {
  app_name: 'dbase',
  alias: {
    find: 'dbase', replacement: '../../../../dbase/static/dbase/js'
  },
  scripts: [{
    srcDir: './dbase/static/dbase/js',
    entry: 'app.js',
    dest: './build/dbase/js/'
  }, {
    srcDir: './dbase/static/dbase/js',
    entry: 'icons.js',
    dest: './build/dbase/js/'
  }],
  styles: {
    src: './dbase/static/dbase/css/app.scss',
    dest: './build/dbase/css/'
  },
  images: {
    src: './dbase/static/dbase/img/**/*',
    dest: './build/dbase/img/'
  },
  staticFiles: [
    {
      src: './node_modules/ckeditor-youtube-plugin/youtube/**/*',
      dest: './build/ckeditor/ckeditor/plugins/youtube'
    },
  ],
};
