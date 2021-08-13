# Adaptive Regime Estimation
This code is based on [Maewal and Bock (2018)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3272080), and calculates which regime the markets currently are in. Please note that this is not the full Modified Risk Parity algorithm, but only contributes to the estimation of the return exponent, α, as described in the paper.

This model then uses the calculations suggested by the paper to create yearly trading signals to determine whether the portfolio should be invested or not, and I use the trading signals generated to trade QQQ on an annual basis. Overall, the model manages to achieve greater risk-adjusted returns than a typical buy and hold strategy.

![stats](https://i.ibb.co/WKtYc3t/1.png)

![performance](https://i.ibb.co/QMG8CdL/Figure-1.png)

![drawdown](https://i.ibb.co/xjkyVW3/Figure-2.png)

## Contact
If you would like to get in touch, my email is aleksandras.v.liauska@bath.edu.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
