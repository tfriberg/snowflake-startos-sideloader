import { i18n } from './i18n'
import { sdk } from './sdk'
import { metricsPort, proxyUdpPortCount, proxyUdpStartPort, uiPort } from './utils'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info(i18n('Starting Snowflake!'))

  const snowflake = sdk.SubContainer.of(
    effects,
    { imageId: 'snowflake' },
    sdk.Mounts.of().mountVolume({
      volumeId: 'main',
      subpath: null,
      mountpoint: '/data',
      readonly: false,
    }),
    'snowflake',
  )

  return sdk.Daemons.of(effects)
    .addDaemon('proxy', {
      subcontainer: snowflake,
      exec: {
        command: [
          'snowflake-proxy',
          '-log',
          '/data/snowflake.log',
          '-metrics',
          '-metrics-address',
          '127.0.0.1',
          '-ephemeral-ports-range',
          `${proxyUdpStartPort}:${proxyUdpStartPort + proxyUdpPortCount - 1}`,
        ],
      },
      ready: {
        display: i18n('Snowflake Proxy'),
        fn: () =>
          sdk.healthCheck.checkPortListening(effects, metricsPort, {
            successMessage: i18n('The proxy is running'),
            errorMessage: i18n('The proxy is not running'),
          }),
      },
      requires: [],
    })
    .addDaemon('dashboard', {
      subcontainer: snowflake,
      exec: {
        command: [
          'busybox-extras',
          'httpd',
          '-f',
          '-p',
          String(uiPort),
          '-h',
          '/www',
        ],
      },
      ready: {
        display: i18n('Dashboard'),
        fn: () =>
          sdk.healthCheck.checkPortListening(effects, uiPort, {
            successMessage: i18n('The dashboard is ready'),
            errorMessage: i18n('The dashboard is not ready'),
          }),
      },
      requires: [],
    })
})
