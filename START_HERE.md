# IIOS — Start Here

**Paquete:** IIOS Complete v1.2.0  
**Fecha de revisión:** 22 de julio de 2026  
**Estado:** Foundation auditada y corregida; pendiente de ratificación del Owner.

## Componentes

1. **IIOS-Foundation-v1.2.0** — gobierno, arquitectura, controles, Claude Code, Cowork, Hermes, conocimiento, roadmap y pruebas.
2. **IIOS-Vault-Template-v1.0.1** — Vault independiente de Obsidian.

## Orden correcto

1. Sustituya en el repositorio los archivos v1.1.0 por esta versión mediante una rama y pull request.
2. Revise `docs/18_AUDIT_DISPOSITION.md`.
3. Ratifique Charter, Constitution y ADR nuevos mediante `docs/20_OWNER_RATIFICATION.md`.
4. Mantenga desconectados o restringidos a solo lectura los conectores de escritura de Cowork.
5. Ejecute `python scripts/verify_foundation.py`.
6. Active el workflow de GitHub y configure manualmente la protección de rama.
7. No instale Hermes, Graphify ni conectores de producción todavía.

## Primera tarea técnica

Después de la ratificación, Claude Code debe aplicar y verificar únicamente controles de repositorio y Foundation. El Governance Core será la siguiente fase; no se crean agentes todavía.

## Regla principal

**Los modelos razonan; Claude Code construye; Cowork investiga bajo supervisión; Obsidian conserva; Graphify relaciona; Hermes opera; Governance autoriza; Audit observa; el Owner decide.**
