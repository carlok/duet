fof(a0,axiom,! [X,Y] : (f(X,g(Y,g(Y,g(X,Y)))) = X)).
fof(a1,axiom,! [X,Y] : (g(X,f(Y,f(Y,f(X,Y)))) = X)).
fof(a2,axiom,! [X,Y] : (f(g(g(g(X,Y),X),X),Y) = Y)).
fof(a3,axiom,! [X,Y] : (g(f(f(f(X,Y),X),X),Y) = Y)).
fof(goal,conjecture,! [X] : (f(X,X) = g(X,X))).
