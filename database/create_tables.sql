CREATE TABLE IF NOT EXISTS ercot_settlement_prices (
	delivery_date DATE,
	hour_ending TEXT,
	settlement_point TEXT,
	settlement_point_price NUMERIC,
	dst_flag TEXT,
    PRIMARY KEY (delivery_date, hour_ending, settlement_point)
);