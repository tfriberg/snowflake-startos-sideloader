import { i18n } from './i18n'
import { sdk } from './sdk'
import { proxyUdpPortCount, proxyUdpStartPort, uiPort } from './utils'

export const setInterfaces = sdk.setupInterfaces(async ({ effects }) => {
  const uiMulti = sdk.MultiHost.of(effects, 'ui-multi')
  const uiMultiOrigin = await uiMulti.bindPort(uiPort, {
    protocol: 'http',
  })
  const ui = sdk.createInterface(effects, {
    name: i18n('Dashboard'),
    id: 'ui',
    description: i18n(
      'NAT type, bandwidth and connections relayed by this proxy',
    ),
    type: 'ui',
    masked: false,
    schemeOverride: null,
    username: null,
    path: '',
    query: {},
  })

  const uiReceipt = await uiMultiOrigin.export([ui])

  const proxyMulti = sdk.MultiHost.of(effects, 'proxy-udp')
  const proxyOrigin = await proxyMulti.bindPortRange({
    internalStartPort: proxyUdpStartPort,
    externalStartPort: proxyUdpStartPort,
    numberOfPorts: proxyUdpPortCount,
  })
  await proxyOrigin.export(
    sdk.createRangeInterface(effects, {
      id: 'proxy-udp',
      name: i18n('Proxy Relay Ports'),
      description: i18n(
        'UDP port range used for WebRTC/ICE peer connections with other Tor clients. Forward this range on your router to get an unrestricted NAT type.',
      ),
    }),
  )

  return [uiReceipt]
})
