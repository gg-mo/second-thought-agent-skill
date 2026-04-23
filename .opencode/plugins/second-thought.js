import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const stripFrontmatter = (content) => {
  const m = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  return m ? m[2] : content;
};

const GATE_MARKER = 'SECOND_THOUGHT_GATE';
const STARTUP_MARKER = 'You have Second Thought';

const HIGH_COMMITMENT_PATTERNS = [
  /\b(commit|merge|ship|deploy|release|publish)\b/i,
  /\b(edit|rewrite|refactor|delete|remove|migrate)\b/i,
  /\b(tool call|run command|execute|apply change|take action)\b/i,
  /\bfinal(ize)?\b/i,
  /\bpre[-_\s]?execution\b/i,
  /\bhigh[-_\s]?risk\b/i,
  /\birreversible\b/i,
];

const ESCAPE_HATCH_PATTERNS = [
  /#st-skip\b/i,
  /\[st:skip[^\]]*\]/i,
  /\bskip second[-_\s]?thought\b/i,
];

const getUserText = (message) =>
  (message?.parts || [])
    .filter((part) => part?.type === 'text' && typeof part.text === 'string')
    .map((part) => part.text)
    .join('\n');

const hasGateMarker = (message) => getUserText(message).includes(GATE_MARKER);
const hasStartupMarker = (message) => getUserText(message).includes(STARTUP_MARKER);

const shouldAutoGate = (text) => HIGH_COMMITMENT_PATTERNS.some((pattern) => pattern.test(text));
const hasEscapeHatch = (text) => ESCAPE_HATCH_PATTERNS.some((pattern) => pattern.test(text));

export const SecondThoughtPlugin = async () => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  const bootstrap = () => {
    const p = path.join(skillsDir, 'using-second-thought', 'SKILL.md');
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
      if (!hasStartupMarker(firstUser)) {
        firstUser.parts.unshift({
          ...firstUser.parts[0],
          type: 'text',
          text: `<EXTREMELY_IMPORTANT>\\n${STARTUP_MARKER}.\\n\\n${content}\\n</EXTREMELY_IMPORTANT>`,
        });
      }

      const latestUser = [...output.messages].reverse().find((m) => m.info.role === 'user');
      if (!latestUser || !latestUser.parts.length || hasGateMarker(latestUser)) return;

      const latestUserText = getUserText(latestUser);
      if (!latestUserText || !shouldAutoGate(latestUserText) || hasEscapeHatch(latestUserText)) return;

      latestUser.parts.unshift({
        ...latestUser.parts[0],
        type: 'text',
        text:
          `<${GATE_MARKER}>\\n` +
          `Automatic checkpoint triggered for a high-commitment request. ` +
          `Before acting, run the second-thought critique and report status/reasoning.\\n\\n` +
          `Escape hatch: include [st:skip <reason>] (or #st-skip) in the user request to bypass once with an explicit reason.\\n` +
          `</${GATE_MARKER}>`,
      });
    },
  };
};
