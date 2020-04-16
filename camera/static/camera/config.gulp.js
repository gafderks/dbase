export default {
  app_name: 'camera',
  alias: {
    find: 'camera', replacement: '../../../../camera/static/camera/js'
  },
  scripts: {
    srcDir: './camera/static/camera/js',
    entry: 'app.js',
    dest: './build/camera/js/'
  },
  styles: {
    src: './camera/static/camera/css/app.scss',
    dest: './build/camera/css/'
  }
};
