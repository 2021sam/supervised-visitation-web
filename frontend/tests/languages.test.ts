import test from 'node:test'
import assert from 'node:assert/strict'
import {
  parseLanguages,
  getAvailableLanguages,
  filterByLanguages,
} from '../src/search/languages.ts'
import type { Supervisor } from '../src/types/supervisor.ts'

function provider(id: number, languages: string): Supervisor {
  return { supervisor_id: id, languages } as Supervisor
}

const providers = [
  provider(1, ''),
  provider(2, 'English'),
  provider(3, '▪ English ▪ Spanish'),
  provider(4, 'Spanish'),
  provider(5, 'English, Spanish, French'),
]

test('Individual language separators', () => {
  assert.deepEqual(
    parseLanguages('English & Spanish; French / Hindi'),
    ['English', 'Spanish', 'French', 'Hindi'],
  )
})

test(' Bullet-separated languages', () => {
  assert.deepEqual(
    parseLanguages('▪ English ▪ Spanish ▪ Hindi'),
    ['English', 'Spanish', 'Hindi'],
  )
})

test('Space-separated languages', () => {
  assert.deepEqual(
    parseLanguages('Spanish Farsi'),
    ['Spanish', 'Farsi'],
  )
})

test('Correct known spelling error', () => {
  assert.deepEqual(parseLanguages('Geman'), ['German'])
})

test('Normalize qualified Mandarin', () => {
  assert.deepEqual(
    parseLanguages('limited Mandarin Capacity'),
    ['Mandarin'],
  )
})

test('English always available', () => {
  assert.deepEqual(getAvailableLanguages([]), ['English'])
})

test('Individual unique language options', () => {
  assert.deepEqual(
    getAvailableLanguages(providers),
    ['English', 'French', 'Spanish'],
  )
})

test('English includes unspecified languages', () => {
  assert.deepEqual(
    filterByLanguages(providers, ['English'])
      .map(p => p.supervisor_id),
    [1, 2, 3, 5],
  )
})

test('All selected languages required', () => {
  assert.deepEqual(
    filterByLanguages(providers, ['English', 'Spanish'])
      .map(p => p.supervisor_id),
    [3, 5],
  )
})

test('Spanish without English requirement', () => {
  assert.deepEqual(
    filterByLanguages(providers, ['Spanish'])
      .map(p => p.supervisor_id),
    [3, 4, 5],
  )
})

test('Case-insensitive matching', () => {
  assert.deepEqual(
    filterByLanguages(providers, ['spanish'])
      .map(p => p.supervisor_id),
    [3, 4, 5],
  )
})

test('No selections returns all providers', () => {
  assert.deepEqual(
    filterByLanguages(providers, []),
    providers,
  )
})
