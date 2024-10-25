/** checks word count of string
 * returns true if word count is greater than max_length
 * @param { string } input_reason
 * @param { number } max_length
 * @returns { boolean }
 */
export function is_within_word_count(input_reason, max_length = 100) {
  return input_reason.length <= max_length;
}

/** given a date, return the lower limit of the valid dates: 2 months before
 * @param { Date } iso_date
 * @returns { string }
 */
export function two_months_before(iso_date) {
  if (typeof iso_date == "string") {
    iso_date = new Date(iso_date);
  }

  const two_months_before = new Date(iso_date);
  two_months_before.setMonth(iso_date.getMonth() - 2);

  return two_months_before.toISOString().split("T")[0];
}

/** given a date, return the upper limit of the valid dates: 3 months after
 * @param { Date } iso_date
 * @returns { string }
 */
export function three_months_after(iso_date) {
  if (typeof iso_date == "string") {
    iso_date = new Date(iso_date);
  }

  const three_months_after = new Date(iso_date);
  three_months_after.setMonth(iso_date.getMonth() + 3);

  return three_months_after.toISOString().split("T")[0];
}