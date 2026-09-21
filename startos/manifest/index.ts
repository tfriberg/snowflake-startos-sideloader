import { setupManifest } from '@start9labs/start-sdk'
import { long, short } from './i18n'

export const manifest = setupManifest({
  id: 'snowflake',
  title: 'Snowflake',
  license: 'BSD-3-Clause',
  packageRepo:
    'https://github.com/Start9-Community/snowflake-startos-sideloader',
  upstreamRepo:
    'https://gitlab.torproject.org/tpo/anti-censorship/pluggable-transports/snowflake',
  marketingUrl: 'https://snowflake.torproject.org/',
  donationUrl: 'https://donate.torproject.org/',
  description: { short, long },
  volumes: ['main'],
  images: {
    snowflake: {
      source: { dockerBuild: {} },
      arch: ['x86_64', 'aarch64'],
    },
  },
  dependencies: {},
})
