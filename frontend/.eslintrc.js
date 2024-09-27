module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: 'tsconfig.json',
    sourceType: 'module',
  },
  reportUnusedDisableDirectives: true,
  extends: ['plugin:@typescript-eslint/recommended', 'next', 'prettier'],
};
