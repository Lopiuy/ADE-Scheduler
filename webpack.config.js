/* global module */
/* global __dirname */

const VueLoaderPlugin = require('vue-loader/lib/plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const pages = [
  'errorhandler/404',
  'errorhandler/500',
  'security/change_password',
  'security/forgot_password',
  'security/login_user',
  'security/register_user',
  'security/reset_password',
  'security/send_confirmation',
  'account',
  'calendar',
  'classroom',
  'help',
  'welcome',
  'contact',
  'whatisnew',
  'contribute',
  'admin',
];

const conf = {
  mode: 'development',
  entry: {},
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
  module: {
    rules: [
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        use: [{
          loader: 'file-loader',
          options: {
            name: '[contenthash].[ext]',
            outputPath: 'img',
            esModule: false
          }
        }]
      },
      {
        test: /\.(sa|sc|c)ss$/,
        use: ['style-loader', 'css-loader', 'sass-loader']
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      inject: false,
      minify: false,
      template: './templates/base.html',
      filename: './html/base.html'
    }),
    new HtmlWebpackPlugin({
      inject: false,
      minify: false,
      template: './templates/custom_macros.html',
      filename: './html/custom_macros.html'
    }),
  ],
  output: {
    path: __dirname + '/static/dist/',
    filename: '[name].bundle.js',
    publicPath: '/static/dist/'
  },
};

pages.forEach(page => {
  let entryPath = `./static/js/${page}.js`;
  let entryName = page.split('/').pop();
  conf.entry[entryName] = entryPath;
  conf.plugins.push(new HtmlWebpackPlugin({
    hash: true,
    inject: false,
    minify: false,
    template: `./templates/${page}.html`,
    filename: `./html/${page}.html`,
    chunks: [entryName],
  }));
});

module.exports = conf;
