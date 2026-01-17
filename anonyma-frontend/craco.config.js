module.exports = {
  style: {
    postcss: {
      mode: 'extends',
      loaderOptions: (postcssLoaderOptions) => {
        postcssLoaderOptions.postcssOptions = {
          ident: 'postcss',
          plugins: [
            require('tailwindcss'),
            require('autoprefixer'),
          ],
        };
        return postcssLoaderOptions;
      },
    },
  },
}
