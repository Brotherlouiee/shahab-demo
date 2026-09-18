import { readFile } from 'node:fs/promises';

const contract = JSON.parse(
  await readFile(new URL('../data/contracts/canonical-identifiers.v1.json', import.meta.url), 'utf8'),
);

const expectedQuestionIds = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'S7', 'S8', 'S10', 'S13'];
const expectedCategoryCounts = {
  maxAmount: 8,
  monthlyInstallment: 6,
  maxRepaymentMonths: 6,
  interestRate: 5,
  depositRequired: 2,
  depositHoldingMonths: 5,
  loanToDepositRatio: 4,
  guaranteeType: 3,
};

function fail(message) {
  throw new Error(`canonical identifier validation failed: ${message}`);
}

function assertUnique(values, name) {
  if (new Set(values).size !== values.length) fail(`${name} contains duplicates`);
}

if (JSON.stringify(contract.questionIds) !== JSON.stringify(expectedQuestionIds)) {
  fail('questionIds differ from the approved questionnaire contract');
}

assertUnique(contract.questionIds, 'questionIds');
assertUnique(Object.keys(contract.questionnaireRouteMap), 'questionnaire routes');

for (const questionId of contract.questionIds) {
  const answerKeys = contract.questions[questionId];
  if (!Array.isArray(answerKeys) || answerKeys.length !== 5) fail(`${questionId} must have exactly five answer keys`);
  assertUnique(answerKeys, `${questionId} answer keys`);
}

for (const [variableId, expectedCount] of Object.entries(expectedCategoryCounts)) {
  const categoryIds = contract.categoryIds[variableId];
  if (!Array.isArray(categoryIds) || categoryIds.length !== expectedCount) {
    fail(`${variableId} must contain ${expectedCount} category ids`);
  }
  assertUnique(categoryIds, `${variableId} category ids`);
}

const routeQuestionIds = Object.values(contract.questionnaireRouteMap);
if (JSON.stringify(routeQuestionIds) !== JSON.stringify(expectedQuestionIds)) {
  fail('route map does not preserve the approved route-to-question mapping');
}

console.log('canonical identifier validation passed');
