import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { Composer } from './Composer';

// Harness controlado para el composer.
function Harness({ onSend, loading = false }: { onSend: (q: string) => void; loading?: boolean }) {
  const [v, setV] = useState('');
  return <Composer value={v} onChange={setV} onSend={() => { onSend(v); setV(''); }} loading={loading} />;
}

describe('Composer', () => {
  it('muestra el contador 0/500 y bloquea menos de 3 caracteres', async () => {
    const user = userEvent.setup();
    render(<Harness onSend={() => {}} />);
    expect(screen.getByText('0/500')).toBeInTheDocument();
    const box = screen.getByLabelText('Pregunta a Sage');
    await user.type(box, 'hi');
    expect(screen.getByText('2/500')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /enviar/i })).toBeDisabled();
  });

  it('Enter envía y Shift+Enter no envía', async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<Harness onSend={onSend} />);
    const box = screen.getByLabelText('Pregunta a Sage');
    await user.type(box, '¿Cómo está SS-01?');
    await user.keyboard('{Enter}');
    expect(onSend).toHaveBeenCalledTimes(1);
    expect(onSend).toHaveBeenCalledWith('¿Cómo está SS-01?');
  });

  it('Ctrl+Enter también envía', async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<Harness onSend={onSend} />);
    const box = screen.getByLabelText('Pregunta a Sage');
    await user.type(box, '¿Y SS-02?');
    await user.keyboard('{Control>}{Enter}{/Control}');
    expect(onSend).toHaveBeenCalledTimes(1);
  });

  it('Shift+Enter inserta salto sin enviar', async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<Harness onSend={onSend} />);
    const box = screen.getByLabelText('Pregunta a Sage') as HTMLTextAreaElement;
    await user.type(box, 'línea uno');
    await user.keyboard('{Shift>}{Enter}{/Shift}');
    expect(onSend).not.toHaveBeenCalled();
    expect(box.value).toContain('\n');
  });

  it('deshabilita el envío mientras carga', () => {
    render(<Harness onSend={() => {}} loading />);
    expect(screen.getByRole('button', { name: /enviar/i })).toBeDisabled();
    expect(screen.getByLabelText('Pregunta a Sage')).toBeDisabled();
  });
});
