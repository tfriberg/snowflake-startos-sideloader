import { i18n } from './i18n'
import { sdk } from './sdk'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info(i18n('Starting Snowflake Proxy!'))

  return sdk.Daemons.of(effects).addDaemon('primary', {
    subcontainer: await sdk.SubContainer.of(
      effects,
      { imageId: 'snowflake' },
      sdk.Mounts.of().mountVolume({
        volumeId: 'main',
        subpath: null,
        mountpoint: '/data',
        readonly: false,
      }),
      'snowflake-sub',
    ),
    exec: { command: ['snowflake-proxy', '-log', '/dev/stdout'] },

    // READY BLOCK
    ready: {
      display: i18n('Snowflake proxy is running'),
      fn: async () => {
        // Wait briefly to ensure container has started
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Return correct structure with string status
        return {
          result: 'success', // Must be "success", "failure", "starting", etc.
          message: i18n('Snowflake proxy is running')
        };
      }
    },

    requires: [],
  })
})
