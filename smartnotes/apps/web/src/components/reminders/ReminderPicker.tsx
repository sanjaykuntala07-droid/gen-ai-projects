import { useState } from 'react';
import { Clock, Calendar, X } from 'lucide-react';
import { addHours, addDays, setHours, setMinutes, startOfDay, nextMonday, format } from 'date-fns';
import { useStore } from '../../store';

interface ReminderPickerProps {
  noteId: string;
  onClose: () => void;
}

export function ReminderPicker({ noteId, onClose }: ReminderPickerProps) {
  const { createReminder } = useStore();
  const [showCustom, setShowCustom] = useState(false);
  const [customDate, setCustomDate] = useState('');
  const [customTime, setCustomTime] = useState('09:00');

  const quickOptions = [
    {
      label: 'In 1 hour',
      icon: <Clock size={14} />,
      getDate: () => addHours(new Date(), 1),
    },
    {
      label: 'Tomorrow morning',
      icon: <Calendar size={14} />,
      getDate: () => setMinutes(setHours(addDays(startOfDay(new Date()), 1), 9), 0),
    },
    {
      label: 'Next week',
      icon: <Calendar size={14} />,
      getDate: () => setMinutes(setHours(nextMonday(new Date()), 9), 0),
    },
  ];

  const handleQuickOption = async (getDate: () => Date) => {
    const date = getDate();
    await createReminder(noteId, date.toISOString());
    onClose();
  };

  const handleCustomSubmit = async () => {
    if (!customDate) return;
    const [hours, minutes] = customTime.split(':').map(Number);
    const date = setMinutes(setHours(new Date(customDate), hours), minutes);
    await createReminder(noteId, date.toISOString());
    onClose();
  };

  return (
    <div className="reminder-picker">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span className="reminder-picker-title" style={{ margin: 0 }}>Set Reminder</span>
        <button className="btn-icon" onClick={onClose} style={{ width: 24, height: 24 }}>
          <X size={14} />
        </button>
      </div>

      {/* Quick options */}
      {quickOptions.map((opt) => (
        <button
          key={opt.label}
          className="reminder-quick-option"
          onClick={() => handleQuickOption(opt.getDate)}
        >
          {opt.icon}
          <span>{opt.label}</span>
          <span style={{
            marginLeft: 'auto',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-text-muted)',
          }}>
            {format(opt.getDate(), 'MMM d, h:mm a')}
          </span>
        </button>
      ))}

      <div style={{
        borderTop: '1px solid var(--color-border-light)',
        margin: '8px 0',
        padding: 0,
      }} />

      {/* Custom */}
      {!showCustom ? (
        <button
          className="reminder-quick-option"
          onClick={() => setShowCustom(true)}
        >
          <Calendar size={14} />
          <span>Custom date & time</span>
        </button>
      ) : (
        <div style={{ padding: '8px 0', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <input
            type="date"
            className="input"
            value={customDate}
            onChange={(e) => setCustomDate(e.target.value)}
            min={format(new Date(), 'yyyy-MM-dd')}
          />
          <input
            type="time"
            className="input"
            value={customTime}
            onChange={(e) => setCustomTime(e.target.value)}
          />
          <button
            className="btn btn-primary"
            onClick={handleCustomSubmit}
            disabled={!customDate}
            style={{ width: '100%', padding: '8px' }}
          >
            Set Reminder
          </button>
        </div>
      )}
    </div>
  );
}
