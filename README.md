# Vending Machines

My project models information that could be useful to someone who owns or manages vending machines. 
It tracks machine owners, locations, types, lanes, products, prices, and sales.

[vending machine erd](vend_erd.png)

## Query I thought it did well on
The few-shot version did well with the question, “How much money has each machine made?” It used a LEFT JOIN between the
machines and their sales, so it included machines with no sales and showed their revenue as $0.00. The zero-shot version 
only showed machines that had sales. The few-shot query gave a more complete answer.

## Question that it tripped up on
The question “Which machines are the closest together?” tripped it up. Both versions subtracted ZIP codes as if they 
were distances:
`ABS(vm1.zip - vm2.zip)`

ZIP codes identify areas; they aren’t measurements of distance. The query found two machines with the same ZIP code, 
but that only shows they share a ZIP code—not that they are the closest machines. To answer the question accurately, 
the database would need location coordinates, or I would need to ask which machines share a ZIP code.

## Multi-shot
For the few-shot strategy, I gave the AI example questions and SQL queries from the vending-machine database. 
The examples seemed to help it use patterns such as LEFT JOIN to include machines with no matching sales or lanes. 
It also returned all the products tied for the largest price difference, while the zero-shot query returned only one.
The examples helped with some query patterns, but they didn’t prevent every mistake. The ZIP-code query still treated 
ZIP codes like distances.

## Conclusion
This project showed me that an AI can turn plain-language questions into useful SQL, especially when I provide the 
schema and examples. However, a query can run successfully and still answer the wrong question. I had to check the SQL 
and its results because the AI could make assumptions that sounded reasonable but weren’t supported by my data.