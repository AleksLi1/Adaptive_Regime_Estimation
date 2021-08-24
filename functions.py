from datetime import datetime, date


def start_of_year(my_date):

    """
    Gives the starting date of a month given any date
    :param my_date: date, str
    :return: str
    """

    my_date = datetime.strptime(my_date, '%Y-%m-%d')
    starting_date = date(my_date.year, 1, 1)
    starting_date = starting_date.strftime('%Y-%m-%d')
    return starting_date

def update_frame(df):
    last_expected = None
    def apply_logic(row):
        nonlocal last_expected
        last_row_id = row.name - 1
        if row.name == 0:
            last_expected = row['Portfolio Value']
            return last_expected
        last_row = df.iloc[[last_row_id]].iloc[0].to_dict()
        last_expected = max(last_expected, last_row['Portfolio Value']) if \
            row['signal'] == 0 else row['Portfolio Value']
        return last_expected
    return apply_logic

