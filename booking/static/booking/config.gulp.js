export default {
  app_name: 'booking',
  alias: {
    find: 'booking', replacement: '../../../../booking/static/booking/js'
  },
  scripts: {
    srcDir: './booking/static/booking/js',
    entry: 'app.js',
    dest: './build/booking/js/'
  },
  styles: {
    src: './booking/static/booking/css/app.scss',
    dest: './build/booking/css/'
  }
};
