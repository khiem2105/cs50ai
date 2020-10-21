import sys

from crossword import *



class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            remains = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    remains.add(word)
            self.domains[var] = remains                 
        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x, y] == None:
            return False
        isRevised = False
        removal = set()
        for word in self.domains[x]:
            if  not self.check_overlap(x, y, word):
                removal.add(word)
                isRevised = True
        for word in removal:
            self.domains[x].remove(word)        
        return isRevised;        
        # raise NotImplementedError

    def check_overlap(self, x, y, word):  
        x_index = self.crossword.overlaps[x, y][0]
        y_index = self.crossword.overlaps[x, y][1]
        for other_word in self.domains[y]:
            if word[x_index] == other_word[y_index]:
                return True
        return False        
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for variable in self.crossword.variables:
                for other_variable in self.crossword.neighbors(variable):
                    arcs.append((variable, other_variable))
        while len(arcs) != 0:
            arc = arcs.pop(0)
            x = arc[0]
            y = arc[1]
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for other_variable in self.crossword.neighbors(x):
                    if (other_variable, x) not in arcs:
                        arcs.append((other_variable, x))    
        return True        
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        return True        
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                continue
            if len(assignment[variable]) != variable.length:
                return False
            for other_variable in assignment:
                if other_variable != variable and assignment[other_variable] == assignment[variable]:
                    return False
            for neighbor in self.crossword.neighbors(variable):
                if neighbor not in assignment:
                    continue
                overlap = self.crossword.overlaps[variable, neighbor]
                if assignment[variable][overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False
        return True            
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def count_ruled_out(word):
            num_ruled_out = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i = self.crossword.overlaps[var, neighbor][0]
                    j = self.crossword.overlaps[var, neighbor][1]
                    for other_word in self.domains[neighbor]:
                        if word[i] != other_word[j]:
                            num_ruled_out += 1
            return num_ruled_out

        remain = [word for word in self.domains[var]]
        remain.sort(key=count_ruled_out)
        return remain
        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variable = []
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassigned_variable.append(variable)
        def count_domain(variable):
            return len(self.domains[variable])
        unassigned_variable.sort(key=count_domain)
        if len(unassigned_variable) >= 2:
            if count_domain(unassigned_variable[0]) == count_domain(unassigned_variable[1]):
                if len(self.crossword.neighbors(unassigned_variable[0])) > len(self.crossword.neighbors(unassigned_variable[1])):
                    return unassigned_variable[0]
                return unassigned_variable[1]
        return unassigned_variable[0]        

                        
        # raise NotImplementedError

    def infer(self, assignment):
        arcs = []
        for assigned_variable in assignment:
            for other_variable in self.crossword.neighbors(assigned_variable):
                if other_variable not in assignment and (other_variable, assigned_variable) not in arcs:
                    arcs.append((other_variable, assigned_variable))
        if self.ac3(arcs):
            return None
        inferrences = {}   
        for variable in self.crossword.variables:
            if variable not in assignment and len(self.domains[variable]) == 1:
                inferrences[variable] = self.domains[variable]
        return inferrences        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                inferrences = self.infer(assignment)
                if inferrences is not None:
                    for new_variable in inferrences:
                        assignment[new_variable] = inferrences[variable]
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else:
                    if inferrences is not None:
                        for new_variable in inferrences:
                            pop = assignment.pop(new_variable)    
        return None                
        # raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
