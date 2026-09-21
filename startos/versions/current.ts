import { IMPOSSIBLE, VersionInfo } from '@start9labs/start-sdk'

export const current = VersionInfo.of({
  version: '2.14.1:4',
  releaseNotes: {
    en_US: "Fixes the UDP port range from 2.14.1:3 so it's actually published to the host — it was narrowed correctly but never reached the container's network interface, so forwarding it on your router had no effect. Forward UDP 30000-30049 to get an unrestricted NAT type; see the instructions for details.",
    es_ES: "Corrige el rango de puertos UDP de 2.14.1:3 para que realmente se publique en el host; se había restringido correctamente pero nunca llegaba a la interfaz de red del contenedor, por lo que reenviarlo en el router no tenía efecto. Reenvía UDP 30000-30049 para obtener un tipo de NAT sin restricciones; consulta las instrucciones para más detalles.",
    de_DE: "Behebt den UDP-Portbereich aus 2.14.1:3, sodass er tatsächlich an den Host weitergegeben wird – er war korrekt eingeschränkt, erreichte aber nie die Netzwerkschnittstelle des Containers, weshalb die Weiterleitung im Router wirkungslos war. Leiten Sie UDP 30000-30049 weiter, um einen uneingeschränkten NAT-Typ zu erhalten. Details siehe Anleitung.",
    pl_PL: "Naprawia zakres portów UDP z 2.14.1:3, tak aby był rzeczywiście publikowany na hoście — był poprawnie zawężony, ale nigdy nie docierał do interfejsu sieciowego kontenera, więc przekierowanie go na routerze nie miało efektu. Przekieruj UDP 30000-30049, aby uzyskać nieograniczony typ NAT. Szczegóły w instrukcji.",
    fr_FR: "Corrige la plage de ports UDP de 2.14.1:3 pour qu'elle soit réellement publiée sur l'hôte : elle était correctement restreinte, mais n'atteignait jamais l'interface réseau du conteneur, si bien que la rediriger sur le routeur n'avait aucun effet. Redirigez le port UDP 30000-30049 pour obtenir un type de NAT non restreint ; voir les instructions pour plus de détails.",
  },
  migrations: {
    up: async ({ effects }) => {},
    down: IMPOSSIBLE,
  },
})
