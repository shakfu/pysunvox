# TODO

## Critical

## High

## Medium

## Low

- [ ] `sv_vorbis_load`: Legacy alias for sv_vplayer_load (deprecated) #unwrapped-api-functions

## Done

- [x] Multi-platform wheel builds (macOS, Linux, Windows) #build-ci
- [x] Aggregate all build artifacts into single download #build-ci

## Notes

- `sv_load_dll`, `sv_load_dll2`, `sv_unload_dll`: Not needed - we use static linking via SUNVOX_STATIC_LIB
- Coverage: 95/96 API functions wrapped (~99%)
