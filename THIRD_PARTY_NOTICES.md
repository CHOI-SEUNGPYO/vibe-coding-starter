# Third-party notices

The following directories contain unmodified source files from
[openai/skills](https://github.com/openai/skills) at commit
`49f948faa9258a0c61caceaf225e179651397431`:

| Local directory | Upstream directory | License |
| --- | --- | --- |
| `skills/playwright` | `skills/.curated/playwright` | Apache-2.0; see `LICENSE.txt` and `NOTICE.txt` |
| `skills/gh-fix-ci` | `skills/.curated/gh-fix-ci` | Apache-2.0; see `LICENSE.txt` |
| `skills/gh-address-comments` | `skills/.curated/gh-address-comments` | Apache-2.0; see `LICENSE.txt` |

Each upstream license and notice is retained in the corresponding directory.
The Playwright license includes attribution to Microsoft Corporation. Other
copyright and attribution notices remain as provided upstream. The root MIT
license does not replace these third-party licenses. Inclusion does not imply
endorsement by OpenAI, Microsoft, or GitHub.

File checksums and source URLs are recorded in `skills.lock.json`. Packages and
services invoked by these skills have their own licenses and terms; their code
is not included merely by including the skill instructions.

The `task-delivery`, `parallel-work`, and `release-check` skills were written for
this repository and are distributed under MIT, with a copy in each directory.

## Community skills

The following public sources are pinned to immutable commits. Upstream skill
files are unchanged except for the UI/UX Pro Max adaptations documented below.
License files copied from repository roots are retained as `LICENSE.txt` in
each corresponding local skill directory.

| Source repository | Commit | Local directories | Declaration |
| --- | --- | --- | --- |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | `7801d061243d7b753bad0e0b3c057cd250b11755` | `skills/ponytail`, `skills/ponytail-review` | MIT; upstream root `LICENSE` |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `39b723ceebf81474d0557c1fecd01eddab585563` | `skills/debugging-and-error-recovery`, `skills/api-and-interface-design` | MIT; upstream root `LICENSE` |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `1f50119f717e935f135d605ce537223d1d7a0dac` | `skills/ui-ux-pro-max` | MIT; upstream root `LICENSE` |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | `skills/vercel-react-best-practices` | MIT as declared by upstream README and SKILL frontmatter |
| [supabase/agent-skills](https://github.com/supabase/agent-skills) | `c9be0e931b7930f7d02126d04774d904c381e7d7` | `skills/supabase-postgres-best-practices` | MIT; upstream root `LICENSE` |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | `d2ef2680594f9a17526a6e1a2e18b3d242c5d17b` | `skills/python-patterns` | MIT; upstream root `LICENSE` |

Vercel does not provide a separate license text file at the pinned commit.
Its unmodified root README, including its MIT declaration, is preserved as
`skills/vercel-react-best-practices/UPSTREAM_README.md`. The original skill's
`license: MIT` and author metadata remain intact. No copyright holder or date
has been invented to fill in missing upstream information.

UI/UX Pro Max was copied from `.claude/skills/ui-ux-pro-max`. Its `SKILL.md`
command examples now use the Codex project installation path
`.agents/skills/ui-ux-pro-max`, with guidance to resolve the script from the
skill location when the working directory differs. A prominent change notice
was added to that file. The search entrypoint also sets
`sys.dont_write_bytecode = True` before importing sibling modules so normal
searches do not add cache files to the pinned skill directory. Search logic,
datasets, provenance records, and supplied tests remain unchanged. Original
SHA-256 values and change descriptions for both modified files are recorded
in `skills.lock.json`.

The UI/UX data includes attribution and license metadata for referenced fonts
and icon libraries. Those metadata files are preserved. The fonts and icon
packages themselves are not installed by this starter. Users of such assets
must retain the applicable attribution and license requirements.

These additions include selected skill directories, not each project's plugin
hooks or global configuration. Inclusion does not imply endorsement by the
listed authors or organizations.

## Reading data example fonts

`examples/reading/data/fonts` bundles Noto Sans KR Regular and Bold, derived at
weights 400 and 700 from the Google Fonts variable font at commit
`b38c5c93af322c45f633e17ac440ec1e6c94d489`. The SIL Open Font License 1.1,
upstream URL and hash, and derived-file hashes are preserved in that directory.
The full variable font is available from its pinned source and is not needed at
runtime. Python/npm dependencies are restored from each example's lock file;
their installed packages are not vendored into this repository.
