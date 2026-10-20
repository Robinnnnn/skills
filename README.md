# Agent skills

Practical agent skills for design, video, and music.

| Skill | What it does |
|---|---|
| [pls-dont-overdesign](skills/pls-dont-overdesign/SKILL.md) | Keep interfaces and visual mockups minimal, with purposeful copy and restrained decoration. |
| [montage](skills/montage/) | Turn photos, Live Photos, and videos into a montage, with optional export to a video editor. |
| [motion-explainer](skills/motion-explainer/SKILL.md) | Render animated explainers and product walkthroughs with Remotion. |
| [dj-set-ripper](skills/dj-set-ripper/SKILL.md) | Extract a DJ set's tracklist and source its individual tracks. |
| [dj-mp3-sourcer](skills/dj-mp3-sourcer/SKILL.md) | Find the requested track version, download accessible audio, or return a purchase link. |

## Install

Run the installer, then choose the skills and agents you use:

```sh
npx skills add Robinnnnn/skills
```

Or copy a folder from [`skills/`](skills/) into your agent's skills directory, including any supporting files. Each skill lists its tool requirements.

For DJ sets, install both DJ skills: `dj-set-ripper` uses `dj-mp3-sourcer` for individual tracks. Their filename helpers use Python 3 and preview changes before applying them.

The motion explainer includes a [reusable production brief](skills/motion-explainer/references/production-prompt.md) and a [fictional example](skills/motion-explainer/references/process-explainer.md). See [package sources](SOURCES.md) for provenance.

## License

Skills, code, and documentation use the [Unlicense](LICENSE). Example photos, screenshots, and videos are for demonstration and are not covered by this license.
