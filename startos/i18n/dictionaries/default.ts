export const DEFAULT_LANG = 'en_US'

const dict = {
  // main.ts
  'Starting Snowflake Proxy!': 0,
  'Snowflake Proxy!': 1,
  'Snowflake proxy is running': 2,
  'Snowflake proxy is not running': 3,

  // interfaces.ts
  'Snowflake Proxy': 4,
  'Snowflake Proxy web interface': 5,

} as const

/**
 * Plumbing. DO NOT EDIT.
 */
export type I18nKey = keyof typeof dict
export type LangDict = Record<(typeof dict)[I18nKey], string>
export default dict
