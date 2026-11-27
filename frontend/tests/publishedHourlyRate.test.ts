import { test } from 'node:test'
import assert from 'node:assert/strict'
import { getPublishedHourlyRate } from '../src/crm/publishedHourlyRate.ts'

const cases = [
  ['$75 per hour', 75],
  ['$60-$90 per hour', '60-90'],
  ['$65 per hour & up', '65+'],
  ['$75 per hour and up', '75+'],
  ['$65-$100+ per hour', '65-100+'],
  ['Starting at $50 per hour', '50+'],
  ['Up to $150 per hour', 'Up to 150'],
  ['$50 per hour weekdays $60 per hour weekends', '50-60'],
  ['$80-$100 (per hour, 2hr minimum)', '80-100'],
  ['$0.00', 0],
  ['Call for pricing', null],
  ['$120', null],
  ['Intake fee $50, Hourly Fee $60', 60],
  ['Intake fee $125, Hourly Fee $55', 55],
  ['$120 Intake Fee, $120 Hourly Fee', 120],
  ['$75 - $125 per hour', '75-125'],
  ['$75 per hour $85 per hour $100 per hour', '75-100'],
  ['Hourly Rate (On-site): $425 per hour; Hourly Rate (Off-site): $660 per hour; Written Summaries / Court Reports: $450/hour per report', '425-660'],
  ['Court Reports: $450/hour per report', null],
  ['$80-$100 (case by case)', null],
] as const

for (const [published, expected] of cases) {
  test(published, () => {
    assert.equal(
      getPublishedHourlyRate(`Published rates: ${published}`),
      expected,
    )
  })
}
