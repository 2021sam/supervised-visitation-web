import { test } from 'node:test'
import assert from 'node:assert/strict'
import { calculateTotal } from '../src/crm/totalCost.ts'
import { createCRMEntry } from '../src/crm/types.ts'

const cases = [
  ['Fixed rate', 175, 2, null, 350],
  ['Numeric string', '120', 2, null, 240],
  ['Dollar prefix', '$100', 2, null, 200],
  ['Location fee', 100, 2, 25, 225],
  ['Fractional hours', 75, 2.5, 20, 207.50],
  ['Decimal rate', '75.50', 2, 10, 161],
  ['Rate range', '60-90', 2, 25, null],
  ['Dollar range', '$60-$90', 2, 25, null],
  ['Starting rate', '75+', 2, 25, null],
  ['Maximum rate', 'Up to 150', 2, 25, null],
  ['Free service', 0, 2, 25, 25],
  ['Missing rate', null, 2, 25, null],
  ['Empty rate', '', 2, 25, null],
  ['Missing hours', 100, null, 25, null],
  ['Zero hours', 100, 0, 25, null],
  ['Negative hours', 100, -2, 25, null],
  ['Negative location fee', 100, 2, -25, null],
  ['Invalid rate', 'unknown', 2, 25, null],
] as const

for (const [name, hourlyQuote, hours, locationFee, expected] of cases) {
  test(name, () => {
    assert.equal(
      calculateTotal({
        ...createCRMEntry(),
        hourlyQuote,
        hours,
        locationFee,
      }),
      expected,
    )
  })
}

test('Default hours is two', () => {
  assert.equal(createCRMEntry().hours, 2)
})

test('Default hours automatically calculates total', () => {
  assert.equal(
    calculateTotal({
      ...createCRMEntry(),
      hourlyQuote: 175,
    }),
    350,
  )
})
