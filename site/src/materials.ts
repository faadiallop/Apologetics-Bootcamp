// The skill's own files, bundled into the Worker when it is built. Nothing is
// fetched at run time, and the text is the same for every trainee of a group,
// so the model's cache can be shared between them.

import skill from "../../skills/apologetics-boot-camp/SKILL.md";
import rules from "../prompts/thought-and-word-rules.md";
import methodology from "../../skills/apologetics-boot-camp/sops/01-methodology-questioning-them-to-death.md";
import bank from "../../skills/apologetics-boot-camp/sops/20-response-bank.md";
import plans from "../../skills/apologetics-boot-camp/sops/21-training-plans.md";

import islamSop from "../../skills/apologetics-boot-camp/sops/10-islam.md";
import islamBank from "../../skills/apologetics-boot-camp/sops/20-response-bank-islam.md";
import islamPlan from "../../skills/apologetics-boot-camp/sops/21-training-plans-islam.md";
import islamFixed from "../../skills/apologetics-boot-camp/fixed/islam.md";

import jwSop from "../../skills/apologetics-boot-camp/sops/11-jehovahs-witnesses.md";
import jwBank from "../../skills/apologetics-boot-camp/sops/20-response-bank-jehovahs-witnesses.md";
import jwPlan from "../../skills/apologetics-boot-camp/sops/21-training-plans-jehovahs-witnesses.md";
import jwFixed from "../../skills/apologetics-boot-camp/fixed/jehovahs-witnesses.md";

import jewishSop from "../../skills/apologetics-boot-camp/sops/12-jewish-people.md";
import jewishBank from "../../skills/apologetics-boot-camp/sops/20-response-bank-jewish-people.md";
import jewishPlan from "../../skills/apologetics-boot-camp/sops/21-training-plans-jewish-people.md";
import jewishFixed from "../../skills/apologetics-boot-camp/fixed/jewish-people.md";

import atheismSop from "../../skills/apologetics-boot-camp/sops/13-atheism.md";
import atheismBank from "../../skills/apologetics-boot-camp/sops/20-response-bank-atheism.md";
import atheismPlan from "../../skills/apologetics-boot-camp/sops/21-training-plans-atheism.md";
import atheismFixed from "../../skills/apologetics-boot-camp/fixed/atheism.md";

import iconSop from "../../skills/apologetics-boot-camp/sops/14-icon-veneration.md";
import iconBank from "../../skills/apologetics-boot-camp/sops/20-response-bank-icon-veneration.md";
import iconPlan from "../../skills/apologetics-boot-camp/sops/21-training-plans-icon-veneration.md";
import iconFixed from "../../skills/apologetics-boot-camp/fixed/icon-veneration.md";

import routerPrompt from "../prompts/router.md";
import memberPrompt from "../prompts/member.md";
import coachPreamble from "../prompts/coach-on-the-site.md";

interface Group {
  name: string;
  sop: string;
  bank: string;
  plan: string;
  fixed: string;
}

export const GROUPS: Record<string, Group> = {
  islam: { name: "Muslims", sop: islamSop, bank: islamBank, plan: islamPlan, fixed: islamFixed },
  "jehovahs-witnesses": { name: "Jehovah's Witnesses", sop: jwSop, bank: jwBank, plan: jwPlan, fixed: jwFixed },
  "jewish-people": { name: "Jewish people", sop: jewishSop, bank: jewishBank, plan: jewishPlan, fixed: jewishFixed },
  atheism: { name: "Atheists", sop: atheismSop, bank: atheismBank, plan: atheismPlan, fixed: atheismFixed },
  "icon-veneration": { name: "Icon veneration", sop: iconSop, bank: iconBank, plan: iconPlan, fixed: iconFixed },
};

const file = (name: string, text: string) => `\n\n<file name="${name}">\n${text.trim()}\n</file>`;

/** The coach's system prompt, in two parts: what every group shares, then this group's own. */
export function coachSystem(groupId: string): [string, string] {
  const g = GROUPS[groupId];
  const shared =
    coachPreamble.trim() +
    file("SKILL.md", skill) +
    file("thought-and-word-rules/SKILL.md", rules) +
    file("sops/01-methodology-questioning-them-to-death.md", methodology) +
    file("sops/20-response-bank.md", bank) +
    file("sops/21-training-plans.md", plans);
  // A draft of the fixed pieces is left out: the skill uses only an approved file,
  // and a draft would be paid for on every turn for nothing.
  const approved = /^Status: approved\s*$/m.test(g.fixed);
  const own =
    `The trainee has chosen this group: ${g.name}. Its materials follow.` +
    file("sops/group-sop.md", g.sop) +
    file("sops/group-response-bank.md", g.bank) +
    file("sops/group-training-plan.md", g.plan) +
    (approved ? file("fixed/group.md", g.fixed) : "\n\nThis group has no approved fixed pieces, so compose those parts yourself.");
  return [shared, own];
}

export function memberSystem(groupId: string): string {
  const g = GROUPS[groupId];
  return (
    memberPrompt.trim() +
    file("shared response bank", bank) +
    file("this group's response bank", g.bank) +
    file("this group's SOP", g.sop)
  );
}

export const routerSystem = (): string => routerPrompt.trim();
