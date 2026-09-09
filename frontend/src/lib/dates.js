const DAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONTH_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

function parse(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

// "Tue 9 Sep" (current year) / "Tue 9 Sep 2025" otherwise
export function shortDay(iso) {
  if (!iso) return 'Unknown';
  const d = parse(iso);
  const yr = d.getFullYear() === new Date().getFullYear() ? '' : ` ${d.getFullYear()}`;
  return `${DAY[d.getDay()]} ${d.getDate()} ${MON[d.getMonth()]}${yr}`;
}

export function longDay(iso) {
  if (!iso) return 'Unknown';
  const d = parse(iso);
  return `${d.getDate()} ${MONTH_LONG[d.getMonth()]} ${d.getFullYear()}`;
}

export const monthName = (m) => MONTH_LONG[Number(m) - 1];
export const todayIso = () => new Date().toISOString().slice(0, 10);
