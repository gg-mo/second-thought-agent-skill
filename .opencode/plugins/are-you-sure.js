import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const stripFrontmatter = (content) => {
  const m = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  return m ? m[2] : content;
};

export const AreYouSurePlugin = async () => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  const bootstrap = () => {
    const p = path.join(skillsDir, 'using-are-you-sure', 'SKILL.md');
    if (!fs.existsSync(p)) return null;
    return stripFrontmatter(fs.readFileSync(p, 'utf8'));
  };

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },
    'experimental.chat.messages.transform': async (_input, output) => {
      const content = bootstrap();
      if (!content || !output.messages.length) return;
      const firstUser = output.messages.find((m) => m.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;
      const marker = 'You have Are You Sure';
      if (firstUser.parts.some((p) => p.type === 'text' && p.text.includes(marker))) return;
      firstUser.parts.unshift({
        ...firstUser.parts[0],
        type: 'text',
        text: `<EXTREMELY_IMPORTANT>\\n${marker}.\\n\\n${content}\\n</EXTREMELY_IMPORTANT>`,
      });
    },
  };
};
