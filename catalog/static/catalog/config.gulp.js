export default {
  app_name: 'catalog',
  alias: {
    find: 'catalog', replacement: '../../../../catalog/static/catalog/js'
  },
  scripts: {
    srcDir: './catalog/static/catalog/js',
    entry: 'app.js',
    dest: './build/catalog/js/'
  },
  styles: {
    src: './catalog/static/catalog/css/app.scss',
    dest: './build/catalog/css/'
  }
};
