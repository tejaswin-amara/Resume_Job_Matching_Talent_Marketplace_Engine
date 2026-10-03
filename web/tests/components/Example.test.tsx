import { expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'

test('Example component test', () => {
  render(<div>Hello Vitest</div>)
  expect(screen.getByText('Hello Vitest')).toBeDefined()
})
