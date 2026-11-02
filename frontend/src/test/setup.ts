import '@testing-library/jest-dom/vitest';
import 'vitest-axe/extend-expect';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Limpia el DOM entre pruebas para aislar cada caso.
afterEach(() => {
  cleanup();
});
