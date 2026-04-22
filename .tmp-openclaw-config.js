{
  meta: {
    lastTouchedVersion: '2026.4.10',
    lastTouchedAt: '2026-04-12T17:23:00.000Z',
  },
  wizard: {
    lastRunAt: '2026-03-31T19:25:03.363Z',
    lastRunVersion: '2026.3.24',
    lastRunCommand: 'doctor',
    lastRunMode: 'local',
  },
  browser: {
    headless: true,
    noSandbox: true,
  },
  auth: {
    profiles: {
      'anthropic:default': {
        provider: 'anthropic',
        mode: 'token',
      },
      'openai-codex:tiarofernandes@gmail.com': {
        provider: 'openai-codex',
        mode: 'oauth',
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: 'openai-codex/gpt-5.4',
        fallbacks: [
          'openai/gpt-5.4',
        ],
      },
      embeddedHarness: {
        runtime: 'codex',
        fallback: 'none',
      },
      models: {
        'anthropic/claude-sonnet-4-6': {
          alias: 'Claude',
        },
        'google/gemini-3.1-flash-lite-preview': {
          alias: 'NanoBanana2',
        },
        'openai-codex/gpt-5.4': {
          alias: 'GPT (Codex)',
        },
        'openai/gpt-5.4': {
          alias: 'GPT (API)',
        },
      },
      workspace: 'cerebro-vital-slim',
      contextTokens: 160000,
      memorySearch: {
        provider: 'openai',
        fallback: 'none',
        model: 'text-embedding-3-small',
      },
      compaction: {
        mode: 'default',
        reserveTokensFloor: 30000,
      },
      timeoutSeconds: 600,
      maxConcurrent: 4,
      subagents: {
        maxConcurrent: 8,
      },
    },
  },
  commands: {
    native: 'auto',
    nativeSkills: 'auto',
    restart: true,
    ownerDisplay: 'raw',
  },
  channels: {
    whatsapp: {
      enabled: true,
      dmPolicy: 'pairing',
      groupPolicy: 'allowlist',
      debounceMs: 0,
      accounts: {
        clinic: {
          enabled: true,
          dmPolicy: 'pairing',
          groupPolicy: 'allowlist',
          debounceMs: 0,
          name: 'Clinic WhatsApp',
        },
      },
      mediaMaxMb: 50,
    },
    telegram: {
      enabled: true,
      dmPolicy: 'allowlist',
      groups: {
        '-1003803476669': {
          requireMention: false,
          groupPolicy: 'allowlist',
          allowFrom: [
            '971050173',
          ],
        },
      },
      allowFrom: [
        '971050173',
      ],
      groupPolicy: 'allowlist',
      streaming: 'partial',
      mediaMaxMb: 19,
    },
  },
  gateway: {
    mode: 'local',
    auth: {
      mode: 'token',
      token: '__OPENCLAW_REDACTED__',
    },
    http: {
      endpoints: {
        chatCompletions: {
          enabled: true,
        },
        responses: {
          enabled: true,
        },
      },
    },
  },
  plugins: {
    load: {
      paths: [
        '/usr/lib/node_modules/openclaw/dist/extensions/whatsapp',
      ],
    },
    entries: {
      whatsapp: {
        enabled: true,
      },
      codex: {
        enabled: true,
      },
    },
  },
  messages: {
    ackReactionScope: 'group-mentions',
  },
}
